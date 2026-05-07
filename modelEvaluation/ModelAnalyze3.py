from pathlib import Path
import re
import argparse

import matplotlib.pyplot as plt


AP_LABELS = [
    'AP @[ .50:.95 ]',
    'AP @[ .50 ]',
    'AP @[ .75 ]',
]

AR_LABELS = [
    'AR @[ maxDets=1 ]',
    'AR @[ maxDets=10 ]',
    'AR @[ maxDets=100 ]',
]

AP_RE = re.compile(
    r'bbox_mAP_copypaste:\s+'
    r'([\d.\-]+)\s+'
    r'([\d.\-]+)\s+'
    r'([\d.\-]+)\s+'
    r'([\d.\-]+)\s+'
    r'([\d.\-]+)\s+'
    r'([\d.\-]+)'
)
EPOCH_RE = re.compile(r'Epoch\(val\)\s+\[(\d+)\]')
AR_RE = re.compile(
    r'Average Recall\s+\(AR\)\s+@\[\s*IoU=0\.50:0\.95\s*\|\s*area=\s*(all|small|medium|large)\s*\|\s*maxDets=\s*(\d+)\s*\]\s*=\s*([\d.\-]+)'
)


def parse_metrics_from_log(log_path):
    """Parse AP/AR metrics from an MMYOLO training log."""
    epochs = []
    ap_data = {label: [] for label in AP_LABELS}
    ar_data = {label: [] for label in AR_LABELS}

    with log_path.open('r', encoding='utf-8', errors='ignore') as file_handle:
        lines = file_handle.readlines()

    for index, line in enumerate(lines):
        epoch_match = EPOCH_RE.search(line)
        if not epoch_match:
            continue

        epoch = int(epoch_match.group(1))

        ap_values = None
        search_start = max(0, index - 20)
        for backward_index in range(index - 1, search_start - 1, -1):
            ap_match = AP_RE.search(lines[backward_index])
            if ap_match:
                ap_values = [float(value) for value in ap_match.groups()]
                break

        if ap_values is None:
            raise ValueError(f'Failed to find AP metrics for epoch {epoch}.')

        ar_values = {}
        for backward_index in range(index - 1, search_start - 1, -1):
            ar_match = AR_RE.search(lines[backward_index])
            if not ar_match:
                continue

            area = ar_match.group(1)
            max_dets = ar_match.group(2)
            value = float(ar_match.group(3))

            if max_dets == '1' and area == 'all':
                ar_values[AR_LABELS[0]] = value
            elif max_dets == '10' and area == 'all':
                ar_values[AR_LABELS[1]] = value
            elif max_dets == '100' and area == 'all':
                ar_values[AR_LABELS[2]] = value
            # elif max_dets == '100' and area == 'medium':
            #     ar_values[AR_LABELS[3]] = value
            # elif max_dets == '100' and area == 'large':
            #     ar_values[AR_LABELS[4]] = value

            if len(ar_values) == len(AR_LABELS):
                break

        if len(ar_values) != len(AR_LABELS):
            raise ValueError(f'Failed to find complete AR metrics for epoch {epoch}.')

        epochs.append(epoch)
        for label, value in zip(AP_LABELS, ap_values[:5]):
            ap_data[label].append(value)
        for label in AR_LABELS:
            ar_data[label].append(ar_values[label])

    return epochs, ap_data, ar_data


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Parse training log file and generate charts.')
    parser.add_argument('--file-name', type=str, default='train_log.log',
                        help='Name of the log file (default: train_log.log)')
    args = parser.parse_args()
    
    # log_path = Path(__file__).with_name('train_log.log')

    # log_path =  Path(__file__).parent 
    # log_path = log_path / '..' / 'logs' / 'train_log.log'  # 适用于Python 3.9及以上版本, 构建日志文件的完整路径

    # 适用于 Python 3.8 及以下：基于脚本目录来拼接相对路径，避免依赖运行时工作目录（cwd）
    log_path = (Path(__file__).resolve().parent / '..' / 'logs' / args.file_name).resolve()
    print(f"Log file path: {log_path}")

    if not log_path.exists():
        raise FileNotFoundError(f'Log file not found: {log_path}')

    epochs, ap_data, ar_data = parse_metrics_from_log(log_path)

    plt.figure(figsize=(14, 8))

    # 从左右排列改为上下排列
    plt.subplot(2, 1, 1) 
    for label, values in ap_data.items():
        plt.plot(epochs, values, marker='o', label=label)
    plt.title('Average Precision (AP) Trends')
    plt.xlabel('Epoch')
    plt.ylabel('Value')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize='small')

    plt.subplot(2, 1, 2)
    for label, values in ar_data.items():
        plt.plot(epochs, values, marker='s', label=label)
    plt.title('Average Recall (AR) Trends')
    plt.xlabel('Epoch')
    plt.ylabel('Value')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize='small')

    plt.tight_layout()
    plt.savefig('trends.png', dpi=200, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    main()