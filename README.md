```markdown
# Iperf Test in VMs

This project focuses on testing the network performance in Virtual Machines (VMs) using the Iperf benchmarking tool. We perform the Iperf tests in two scenarios: standalone tests, and when multiple VMs compete for resources.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Linux or Unix-based system
- Iperf installed on your machine

## Usage

### 1. Iperf Testing

Use the bash script `iperf_test.sh` to run the Iperf tests. You can configure the test by specifying command-line options:

```bash
./iperf_test.sh [-i IP] [-d BASE_DIR] [-u DURATION] [-w WINDOW_SIZE] [-m Message_SIZE] [-t TEST_TIMES] [-l LOOP_ON] [-s START_VALUE] [-e END_VALUE]
```

Options:

- `-i` IP address (default: `20.0.1.4`)
- `-d` Base directory for output files (default: directory of this script)
- `-u` Duration (default: `60`)
- `-w` Window size (default: `2m`)
- `-m` Message size (default: `1500`)
- `-t` Test times (default: `5`)
- `-l` What to loop on (options: `duration`, `window_size`, `message_size`, `parallel` - default: `parallel`)
- `-s` Start value for loop (default: `1`)
- `-e` End value for loop (default: `5`)

### 2. Analyzing the Result

Use the Python script `analyze_result.py` to parse the Iperf test result and write the data to a CSV file:

```bash
python3 analyze_result.py
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
```

Please customize this to fit your project's needs. For example, if you don't have a `CONTRIBUTING.md` or `LICENSE.md` file, you might want to remove the "Contributing" and "License" sections, or modify them to provide the appropriate information. Also, ensure to change file names (like `iperf_test.sh` and `analyze_result.py`) as per your actual files.
