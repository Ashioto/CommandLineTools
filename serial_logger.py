import argparse
import serial
import time
from datetime import datetime
import os


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='串口数据记录器，将串口数据保存到TXT文件')
    parser.add_argument('port', help='串口号，例如 COM3 或 /dev/ttyUSB0')
    parser.add_argument('baudrate', type=int, help='波特率，例如 9600, 115200')
    parser.add_argument('duration', type=int, help='数据保存时间(秒)')
    parser.add_argument('-o', '--output', help='输出文件路径，默认使用当前时间作为文件名')

    args = parser.parse_args()

    # 设置输出文件名
    if args.output:
        filename = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"serial_data_{timestamp}.txt"

    try:
        # 打开串口
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baudrate,
            timeout=1  # 超时时间1秒
        )

        # 检查串口是否打开
        if not ser.is_open:
            print(f"无法打开串口 {args.port}")
            return

        print(f"已打开串口 {args.port}，波特率 {args.baudrate}")
        print(f"将记录 {args.duration} 秒的数据到文件: {filename}")

        # 打开文件准备写入
        with open(filename, 'w', encoding='utf-8') as f:
            # 记录开始时间
            start_time = time.time()
            f.write(f"=== 串口数据记录开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write(f"=== 串口号: {args.port}, 波特率: {args.baudrate} ===\n\n")

            print("开始记录数据... (按Ctrl+C停止)")

            try:
                # 循环读取数据，直到达到指定时间
                while time.time() - start_time < args.duration:
                    # 读取串口数据
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting)
                        # 尝试解码为字符串，失败则保存原始十六进制
                        try:
                            text = data.decode('utf-8')
                        except UnicodeDecodeError:
                            text = f"[二进制数据]: {data.hex()}\n"

                        # 打印到控制台
                        print(text, end='')
                        # 写入文件
                        f.write(text)
                        # 刷新缓冲区，确保数据及时写入
                        f.flush()

                    # 短暂延迟，减少CPU占用
                    time.sleep(0.01)

            except KeyboardInterrupt:
                print("\n用户中断记录")

            # 记录结束时间
            f.write(f"\n\n=== 串口数据记录结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

        # 关闭串口
        ser.close()
        print(f"数据记录完成，已保存到 {filename}")
        print(f"实际记录时间: {time.time() - start_time:.2f} 秒")

    except serial.SerialException as e:
        print(f"串口错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()

