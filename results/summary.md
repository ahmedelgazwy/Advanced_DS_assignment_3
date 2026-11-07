# Benchmark summary (results)

## Log-log slopes of time against n + m (1 = linear)

```
algorithm                   FRB (both forms)  random G(n, 5n)
--------------------------  ----------------  ---------------
basic VC                                1.09             1.01
randomized VC                           1.06             1.01
greedy, natural order                   0.94             1.06
greedy, smallest-last                   1.01             1.07
smallest-last order only                1.00             1.05
greedy pass along SL order              0.95             1.07
```

## FRB running time (ms, mean of the instances' medians)

```
family     form  m          basic_vc  randomized_vc  natural_coloring  sl_coloring  sl_order  sl_greedy
---------  ----  ---------  --------  -------------  ----------------  -----------  --------  ---------
frb30-15   clq      83,198       7.5            7.7              10.7         60.5      46.8       10.6
frb30-15   mis      17,827       1.0            1.1               2.5         13.0      10.6        2.8
frb35-17   clq     148,791      13.0           12.7              18.0        104.2      90.0       21.5
frb35-17   mis      27,924       1.8            2.7               5.0         19.3      16.1        4.6
frb40-19   clq     247,041      20.3           20.5              31.1        166.2     134.9       29.2
frb40-19   mis      41,379       2.4            2.4               5.7         26.3      23.4        5.8
frb45-21   clq     387,403      31.5           31.9              43.8        259.8     210.0       50.5
frb45-21   mis      58,637       3.3            3.4               7.9         38.6      32.7        9.0
frb50-23   clq     580,218      50.4           49.8              68.5        430.6     342.2       75.2
frb50-23   mis      80,457       5.3            5.3              11.6         57.6      44.7       11.6
frb53-24   clq     714,121      59.5           57.5              89.0        476.1     393.4       86.8
frb53-24   mis      94,235       5.5            5.7              12.6         60.4      49.0       12.5
frb59-26   clq   1,049,452      87.9           92.1             124.1        697.5     579.2      132.1
frb59-26   mis     126,359       7.7            7.5              17.1         81.3      67.7       17.5
frb100-40  clq   7,425,226     462.8          464.3             902.0       5420.3    4145.1      951.4
frb100-40  mis     572,774      38.5           36.5              77.3        405.9     309.7       78.5
```

## FRB solution quality (mean over the family's instances)

Vertex cover on the mis form (OPT exact); colors on the clq form (chi exact). `file` = the file's numbering, `relab` = mean over randomly relabeled copies.

```
family     OPT   basic file  basic relab  rand file  rand relab  chi  natural file  natural relab  SL file  SL relab  d+1   Delta+1
---------  ----  ----------  -----------  ---------  ----------  ---  ------------  -------------  -------  --------  ----  -------
frb30-15    420       449.6        444.5      447.9       440.3   30          30.0           87.8     51.4      50.2   338      404
frb35-17    560       592.4        589.1      591.8       583.1   35          35.0          113.7     59.2      60.4   459      550
frb40-19    720       758.4        753.4      757.5       746.5   40          40.0          137.8     63.2      68.0   600      699
frb45-21    900       943.2        937.7      941.9       931.0   45          45.0          168.0     74.2      77.2   766      874
frb50-23   1100      1148.4       1141.8     1146.5      1133.6   50          50.0          195.6     82.4      83.8   948     1075
frb53-24   1219      1272.0       1264.6     1269.1      1256.1   53          53.0          212.8     78.8      81.4  1059     1189
frb59-26   1475      1534.0       1524.8     1531.1      1515.1   59          59.0          247.5     99.6      96.6  1290     1444
frb100-40  3900      4000.0       3985.3     3995.0      3972.0  100         100.0          560.0    151.0     145.3  3572     3865
```

## Peak extra memory (tracemalloc)

```
graph                n          m          algorithm                 KiB     bytes/vertex
-------------------  ---------  ---------  ------------------------  ------  ------------
G(n,5n) n=10,000        10,000     50,000  basic VC                     326         33.39
G(n,5n) n=10,000        10,000     50,000  randomized VC                301         30.84
G(n,5n) n=10,000        10,000     50,000  greedy, natural order        502         51.38
G(n,5n) n=10,000        10,000     50,000  greedy, smallest-last        502         51.40
G(n,5n) n=10,000        10,000     50,000  smallest-last order only     469         48.04
G(n,5n) n=100,000      100,000    500,000  basic VC                   3,361         34.42
G(n,5n) n=100,000      100,000    500,000  randomized VC              3,067         31.41
G(n,5n) n=100,000      100,000    500,000  greedy, natural order      5,072         51.94
G(n,5n) n=100,000      100,000    500,000  greedy, smallest-last      5,072         51.94
G(n,5n) n=100,000      100,000    500,000  smallest-last order only   4,732         48.46
G(n,5n) n=1,000,000  1,000,000  5,000,000  basic VC                  33,164         33.96
G(n,5n) n=1,000,000  1,000,000  5,000,000  randomized VC             30,294         31.02
G(n,5n) n=1,000,000  1,000,000  5,000,000  greedy, natural order     50,775         51.99
G(n,5n) n=1,000,000  1,000,000  5,000,000  greedy, smallest-last     50,775         51.99
G(n,5n) n=1,000,000  1,000,000  5,000,000  smallest-last order only  47,359         48.50
frb30-15-1 clq             450     83,198  basic VC                      10         22.24
frb30-15-1 clq             450     83,198  randomized VC                 12         28.20
frb30-15-1 clq             450     83,198  greedy, natural order         17         38.15
frb30-15-1 clq             450     83,198  greedy, smallest-last         25         55.77
frb30-15-1 clq             450     83,198  smallest-last order only      25         55.77
frb59-26-1 clq           1,534  1,049,256  basic VC                      49         32.53
frb59-26-1 clq           1,534  1,049,256  randomized VC                 52         34.50
frb59-26-1 clq           1,534  1,049,256  greedy, natural order         72         47.94
frb59-26-1 clq           1,534  1,049,256  greedy, smallest-last         98         65.33
frb59-26-1 clq           1,534  1,049,256  smallest-last order only      98         65.33
```

## Worst cases (first = basic VC / natural order; second = randomized VC mean / smallest-last)

```
problem       graph                             optimum  first  second   range
------------  --------------------------------  -------  -----  -------  ---------
vertex cover  perfect matching, 1000 edges         1000   2000  1000.00  1000-1000
vertex cover  complete bipartite K100,100           100    200   185.23    165-198
vertex cover  star, 1000 leaves                       1      2     2.00        1-8
vertex cover  complete graph K50                     49     50    49.00      49-49
coloring      crown graph, 200 vertices               2    100        2        2-2
coloring      binomial tree B12, 4096 vertices        2     13        2        2-2
coloring      complete graph K50                     50     50       50      50-50
```
