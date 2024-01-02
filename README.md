# MLAI CLI TOOL

Made by Heejun Lee, 2023

## Install

1. Git clone this repository
2. Ask Heejun and get some secrets file.
3. Add a repository directory in your PATH
4. Ready to go!

## Usages

### Find Me Free Gpus Tool

This tool finds an empty gpu in our cluster using `freegpu` command.

You can query free gpu in everywhere in the KAIST network. This script uses the Grafana backend.

```sh
(base) ainl@ainl-h470-hd3:~/library/mlai-cli$ mlai freegpu --fp16 13
[MLAI-CLI:freegpu] GpuInstance(node=GpuNode(server_name, n_gpus=8), index=0, name=2080Ti, mem=4.9%, compute=0.0%, spec=GpuSpec(fp32=13.6, fp16=57, bf16=0, vram=11))
[MLAI-CLI:freegpu] 1 / 1 are free
```

```sh
(base) ainl@ainl-h470-hd3:~/library/mlai-cli$ mlai freegpu -h
usage: mlai [-h] [--fp32 FP32] [--bf16 BF16] [--fp16 FP16] [--mem MEM]

optional arguments:
  -h, --help   show this help message and exit
  --fp32 FP32  Limit lower bound of FP32 TFLOPs
  --bf16 BF16  Limit lower bound of BF16 TFLOPs. You can use this to filter out older gpu than Ampere.
  --fp16 FP16  Limit lower bound of FP16 TFLOPs
  --mem MEM    Limit lower bound of VRAM in GB
```

### IOStat Tool

This tool is for monitoring disk input-output using `iostat` command. 

However, this tool will compute transferred bytes per transaction. This is needed to measure how much Infiniband is loaded efficiently. Higher bytes per transaction should be better.

**This tool only inspects local disks. So, to monitor the shared disk, you should actually run this script on the right server.**

```sh
heejun@st1:~/library/mlai-cli$ ./mlai iostat
[MLAI-CLI:iostat.main] sdb per_transaction: 55.2 KB/T read: 6.4 MB/S write: 12.8 MB/S
[MLAI-CLI:iostat.main] sdb per_transaction: 44.0 KB/T read: 5.1 MB/S write: 9.6 MB/S
[MLAI-CLI:iostat.main] sdb per_transaction: 78.2 KB/T read: 4.4 MB/S write: 38.5 MB/S
```

## Contribution

You **have to be careful about the security of our server cluster if you wanna commit something here!**

- Do not reveal any **addresses**
- Do not reveal any **detailed server structures**
- Do not reveal any **RPC ports**
- Do not reveal any **directory structure**

Keep those things in the `mlai_cli/secrets` module. Ask Heejun to get secrets.
