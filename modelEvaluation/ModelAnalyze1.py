import re
import argparse
import matplotlib.pyplot as plt
import pathlib as Path

def parse_log(log_path):
    epochs = []
    iterations = []
    base_lrs = []
    lrs = []
    losses = []
    loss_clss = []
    loss_bboxes = []
    loss_dfls = []

    # Regex to match the log lines
    # Example: 04/28 16:08:44 - mmengine - INFO - Epoch(train)  [1][8/8]  base_lr: 1.0000e-02 lr: 7.0000e-05  eta: 2:07:07  time: 1.1396  data_time: 0.1601  memory: 17208  grad_norm: 1640.7580  loss: 13.9161  loss_cls: 9.3905  loss_bbox: 1.2588  loss_dfl: 3.2669
    pattern = re.compile(
        r'Epoch\(train\)\s+\[(\d+)\]\[(\d+)/\d+\]\s+base_lr:\s+([\d\.e-]+)\s+lr:\s+([\d\.e-]+).*?loss:\s+([\d\.]+)\s+loss_cls:\s+([\d\.]+)\s+loss_bbox:\s+([\d\.]+)\s+loss_dfl:\s+([\d\.]+)'
    )

    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                epochs.append(int(match.group(1)))
                iterations.append(len(iterations) + 1)
                base_lrs.append(float(match.group(3)))
                lrs.append(float(match.group(4)))
                losses.append(float(match.group(5)))
                loss_clss.append(float(match.group(6)))
                loss_bboxes.append(float(match.group(7)))
                loss_dfls.append(float(match.group(8)))

    return iterations, base_lrs, lrs, losses, loss_clss, loss_bboxes, loss_dfls

# Parse command line arguments
parser = argparse.ArgumentParser(description='Parse training log file and generate charts.')
parser.add_argument('--file-name', type=str, default='train_log.log',
                    help='Name of the log file (default: train_log.log)')
args = parser.parse_args()

# Try parsing log file
log_path = (Path(__file__).resolve().parent / '..' / 'logs' / args.file_name).resolve()
iters, base_lrs, lrs, losses, loss_clss, loss_bboxes, loss_dfls = parse_log(log_path)
# iters是什么？它是一个列表，记录了训练过程中每个日志行对应的迭代次数（iteration）。
# 在日志中，每当模型完成一个训练步骤（即处理一批数据）时，就会记录一次迭代。
# 这个列表可以用来绘制学习率和损失随迭代次数变化的曲线，从而分析模型的训练过程。

# if not iters:
#     # If second log is empty or format differs, try first log
#     iters, base_lrs, lrs, losses, loss_clss, loss_bboxes, loss_dfls = parse_log('first_train_log.log')

if iters:
    plt.figure(figsize=(15, 10))

    # Plot 1: Learning Rate
    plt.subplot(2, 2, 1)
    plt.plot(iters, base_lrs, label='base_lr', linestyle='--')
    plt.plot(iters, lrs, label='lr')
    plt.title('Learning Rate over Iterations')
    plt.xlabel('Iteration')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)

    # Plot 2: Total Loss
    plt.subplot(2, 2, 2)
    plt.plot(iters, losses, label='total loss', color='red')
    plt.title('Total Loss over Iterations')
    plt.xlabel('Iteration')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    # Plot 3: Specific Losses
    plt.subplot(2, 2, 3)
    plt.plot(iters, loss_clss, label='loss_cls')
    plt.plot(iters, loss_bboxes, label='loss_bbox')
    plt.plot(iters, loss_dfls, label='loss_dfl')
    plt.title('Component Losses over Iterations')
    plt.xlabel('Iteration')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    # Plot 4: Normalized Component Losses (to see relative trends)
    plt.subplot(2, 2, 4)
    # Just show loss_cls and loss_bbox together for clarity
    plt.plot(iters, loss_clss, label='loss_cls')
    plt.plot(iters, loss_bboxes, label='loss_bbox')
    plt.title('Cls vs Bbox Loss')
    plt.xlabel('Iteration')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('training_curves.png')
    print("Chart generated successfully as training_curves.png")
else:
    print("No data found in logs.")


