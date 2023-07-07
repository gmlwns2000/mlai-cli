# MLAI CLI TOOL

Made by Heejun Lee, 2023

## Usages

### IOStat Tool

This tool is for monitoring disk input-output using `iostat` command. 

However, this tool will compute transferred bytes per transaction. This is needed to measure how much Infiniband is loaded efficiently. Higher bytes per transaction should be better.

**This tool only inspects local disks. Therefore, to monitor the shared disk, you should run this script on the proper server.**

```sh
heejun@st1:~/library/mlai-cli$ ./mlai iostat
[MLAI-CLI:iostat.main] sdb per_transaction: 55.2 KB/T read: 6.4 MB/S write: 12.8 MB/S
[MLAI-CLI:iostat.main] sdb per_transaction: 44.0 KB/T read: 5.1 MB/S write: 9.6 MB/S
[MLAI-CLI:iostat.main] sdb per_transaction: 78.2 KB/T read: 4.4 MB/S write: 38.5 MB/S
```
