import re
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Load the log file
log_path = (Path(__file__).resolve().parent / '..' / 'logs' / 'train_log.log').resolve()
with open(log_path, 'r') as f:
    log_content = f.readlines()

# Lists to store metrics
data = []

# Regex pattern to extract relevant metrics
# Example: Epoch(train)   [1][8/8]  base_lr: 1.0000e-02 lr: 7.0000e-05 ... loss: 4.8856  loss_cls: 2.1524  loss_bbox: 1.1396  loss_dfl: 1.5936
pattern = re.compile(
    r'Epoch\(train\)\s+\[(?P<epoch>\d+)\]\[(?P<iter>\d+)/\d+\].*?'
    r'base_lr:\s+(?P<base_lr>[\d.e+-]+)\s+'
    r'lr:\s+(?P<lr>[\d.e+-]+).*?'
    r'loss:\s+(?P<loss>[\d.]+)\s+'
    r'loss_cls:\s+(?P<loss_cls>[\d.]+)\s+'
    r'loss_bbox:\s+(?P<loss_bbox>[\d.]+)\s+'
    r'loss_dfl:\s+(?P<loss_dfl>[\d.]+)'
)

for line in log_content:
    match = pattern.search(line)
    if match:
        data.append({
            'epoch': int(match.group('epoch')),
            'iter': int(match.group('iter')),
            'base_lr': float(match.group('base_lr')),
            'lr': float(match.group('lr')),
            'loss': float(match.group('loss')),
            'loss_cls': float(match.group('loss_cls')),
            'loss_bbox': float(match.group('loss_bbox')),
            'loss_dfl': float(match.group('loss_dfl'))
        })

# Create DataFrame
df = pd.DataFrame(data)

if df.empty:
    print("No data extracted. Please check regex or log format.")
else:
    # Create a global step index for plotting
    df['step'] = range(len(df))

    # Plotting
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # 1. Learning Rate Plot
    axes[0].plot(df['step'], df['base_lr'], label='base_lr', linestyle='--', color='gray')
    axes[0].plot(df['step'], df['lr'], label='lr', color='blue')
    axes[0].set_title('Learning Rate Over Time')
    axes[0].set_ylabel('LR Value')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 2. Loss Plot
    axes[1].plot(df['step'], df['loss'], label='Total Loss', linewidth=2, color='black')
    axes[1].plot(df['step'], df['loss_cls'], label='loss_cls', alpha=0.8)
    axes[1].plot(df['step'], df['loss_bbox'], label='loss_bbox', alpha=0.8)
    axes[1].plot(df['step'], df['loss_dfl'], label='loss_dfl', alpha=0.8)
    axes[1].set_title('Training Losses Over Time')
    axes[1].set_xlabel('Iteration Step')
    axes[1].set_ylabel('Loss Value')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    # plt.show()
    plt.savefig('training_curves2.png')
    print("Chart generated successfully as training_curves2.png")

    # Summarize final values
    print(df.tail(1).to_dict(orient='records')[0])