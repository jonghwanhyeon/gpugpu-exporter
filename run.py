from gpugpu_exporter import GPUGPUExporter


if __name__ == "__main__":
    exporter = GPUGPUExporter(port=9700, interval=60)
    exporter.start_server()
