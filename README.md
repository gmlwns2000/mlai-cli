# MLAI CLI TOOL

Made by Heejun Lee 2023

## Usages

### IOStat Tool

This tool is for monitering disk input output, using `iostat` command. 

However this tool will compute trasferred bytes per transaction. This is needed for measure how much is Infiniband loaded efficiently. Higher bytes per transaction should be better.

```sh
$ ./mlai iostat
```