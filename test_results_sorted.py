import csv
import glob
import os


def process_test_logs(log_dir, output_csv):
    parsed_data = []

    # 1. 取得指定資料夾內所有 txt 日誌檔
    file_list = glob.glob(os.path.join(log_dir, "*.txt"))

    for file_path in file_list:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline().strip(), f.readline().strip()]

            # 確保檔案至少有前兩行
            if len(lines) < 2 or not lines[0] or not lines[1]:
                continue

            line1_parts = [p.strip() for p in lines[0].split("|")]
            line2_parts = [p.strip() for p in lines[1].split("|")]

            sn = ""
            serial_number = ""
            start_timestamp = ""
            duration_sec = 0

            # 解析第一行 {@BATCH：取得 板卡識別序號 (SN)
            # 格式: {@BATCH|板卡名稱||SN|...} -> line1_parts[3]
            if line1_parts[0].startswith("{@BATCH") and len(line1_parts) >= 4:
                sn = line1_parts[3]

            # 解析第二行 {@BTEST：取得 序號, 開始時間戳記, 測試總耗時
            # 格式: {@BTEST|Serial_Number|00|Start_Timestamp|Test_Duration_Sec|...}
            if line2_parts[0].startswith("{@BTEST") and len(line2_parts) >= 5:
                serial_number = line2_parts[1]
                start_timestamp = line2_parts[3]
                try:
                    duration_sec = int(line2_parts[4])
                except ValueError:
                    duration_sec = 0

            # 確保必要欄位皆有擷取到
            if serial_number and start_timestamp:
                parsed_data.append({
                    "Serial_Number": serial_number,
                    "SN": sn,
                    "Start_Timestamp": start_timestamp,
                    "Test_Duration_Sec": duration_sec,
                })

    # 2. 依照 [該張主板測試開始時間戳記 (Start_Timestamp)] 升冪排序
    parsed_data.sort(key=lambda x: x["Start_Timestamp"])

    # 3. 儲存為 CSV 檔案 (格式對齊 test_results_sorted_sample.csv)
    fieldnames = ["Serial_Number", "SN", "Start_Timestamp", "Test_Duration_Sec"]
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed_data)

    print(f"處理完成！共解析 {len(parsed_data)} 筆資料，已輸出至: {output_csv}")


if __name__ == "__main__":
    LOG_FOLDER = r"d:\ICT_CT_extract\log_files"  # 日誌資料夾路徑
    OUTPUT_FILE = r"d:\ICT_CT_extract\test_results_sorted.csv"

    process_test_logs(LOG_FOLDER, OUTPUT_FILE)