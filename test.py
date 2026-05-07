# from pathlib import Path

# root = Path(r"E:\GraduateStudy\Lesson\计算机视觉\2023认领一个潜点水下垃圾照片 (水下&陆地,已脱敏)")
# target_text = "水下垃圾照片 "

# renamed_count = 0
# skipped_count = 0

# for file_path in root.rglob("*"):
#     if not file_path.is_file():
#         continue

#     old_name = file_path.name
#     if target_text not in old_name:
#         print(f"跳过（未找到目标文本）: {old_name}")
#         continue

#     new_name = old_name.replace(target_text, "")
#     new_path = file_path.with_name(new_name)

#     if new_path.exists():
#         print(f"跳过（目标已存在）: {new_path}")
#         skipped_count += 1
#         continue

#     file_path.rename(new_path)
#     print(f"已重命名: {file_path} -> {new_path}")
#     renamed_count += 1

# print(f"\n完成：重命名 {renamed_count} 个文件，跳过 {skipped_count} 个文件。")






"""Compare filenames (without extension) between two folders.

Usage:
  python test.py --src A_FOLDER --ref B_FOLDER [--dry-run] [--verbose]

For each file in `src`, if there is no file in `ref` with the same name (ignoring extension),
the file in `src` will be moved to the Recycle Bin. Uses `send2trash` if available,
otherwise falls back to Windows API.
"""

import argparse
import os
from pathlib import Path
import sys
import ctypes


def try_import_send2trash():
	try:
		import send2trash

		return send2trash.send2trash
	except Exception:
		return None


def send_to_recycle_bin_windows(path: str): # 这个函数使用 Windows API 将文件移动到回收站
	# Fallback using SHFileOperationW
	from ctypes import wintypes

	class SHFILEOPSTRUCTW(ctypes.Structure):
		_fields_ = [
			("hwnd", wintypes.HWND),
			("wFunc", ctypes.c_uint),
			("pFrom", wintypes.LPCWSTR),
			("pTo", wintypes.LPCWSTR),
			("fFlags", ctypes.c_uint),
			("fAnyOperationsAborted", wintypes.BOOL),
			("hNameMappings", ctypes.c_void_p),
			("lpszProgressTitle", wintypes.LPCWSTR),
		]

	FO_DELETE = 3
	FOF_ALLOWUNDO = 0x40
	FOF_NOCONFIRMATION = 0x10

	p_from = str(path) + "\0\0"  # double-null terminated

	op = SHFILEOPSTRUCTW()
	op.hwnd = None
	op.wFunc = FO_DELETE
	op.pFrom = p_from
	op.pTo = None
	op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION

	res = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
	if res != 0:
		raise OSError(f"SHFileOperationW failed with code {res}")


def build_ref_stem_set(ref_dir: Path): # 构建一个集合，包含 ref_dir 中所有文件的 stem（不带扩展名的部分）
	stems = set()
	for p in ref_dir.iterdir():
		if p.is_file():
			stems.add(p.stem)
	return stems


def main():
	parser = argparse.ArgumentParser(description="Compare filenames (no suffix) and recycle unmatched files.")
	parser.add_argument("--src", required=True, help="Source folder to scan (A)")
	parser.add_argument("--ref", required=True, help="Reference folder to compare against (B)")
	parser.add_argument("--dry-run", action="store_true", help="Do not actually delete, only show actions")
	parser.add_argument("--verbose", action="store_true", help="Verbose output")
	# Recursively iterate all files under src (including subdirectories)
	args = parser.parse_args()

	src = Path(args.src) # source folder A
	ref = Path(args.ref) # reference folder B

	if not src.exists() or not src.is_dir():
		print(f"Source folder does not exist or is not a directory: {src}")
		sys.exit(2)
	if not ref.exists() or not ref.is_dir():
		print(f"Reference folder does not exist or is not a directory: {ref}")
		sys.exit(2)

	ref_stems = build_ref_stem_set(ref)

	sender = try_import_send2trash() # try to use send2trash if available
	if sender is None:
		if os.name == "nt":
			sender = send_to_recycle_bin_windows
		else:
			print("send2trash not installed and no fallback available on this OS.")
			print("Install send2trash (pip install send2trash) to enable recycle-bin deletion.")
			sender = None

	for p in src.rglob("*"): # src.rglob("*") 代表递归地遍历 src 文件夹下的所有文件和子文件夹
		if not p.is_file():
			continue
		name = p.stem
		if name in ref_stems:
			if args.verbose:
				try:
					rel = p.relative_to(src)
				except Exception:
					rel = p
				print(f"Keep: {rel} (matched by name '{name}')")
			continue

		# not found in ref
		try:
			rel = p.relative_to(src)
		except Exception:
			rel = p

		if args.dry_run:
			print(f"Would recycle: {rel}")
			continue

		if sender is None:
			# as a last resort, do a permanent delete after warning
			print(f"Permanently deleting (no recycle available): {rel}")
			p.unlink()
			continue

		try:
			sender(str(p))
			print(f"Recycled: {rel}")
		except Exception as e:
			print(f"Failed to recycle {rel}: {e}")


if __name__ == "__main__":
	main()