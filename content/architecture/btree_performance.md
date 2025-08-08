+++
title = "Btree Performance"
slug = "BtreePerformance"
url = "/Architecture/BtreePerformance/"
+++

Here's some btree microbenchmarks, taken September 2023, on a Ryzen 5950X,
turbothreading and hyperthreading off:

    rand_insert: 10M  with  1 threads in   15 sec,  1480 nsec per iter,  660K per sec
    rand_insert: 10M  with 16 threads in    4 sec,  6330 nsec per iter, 2.41M per sec
    rand_lookup: 10M  with  1 threads in    7 sec,   736 nsec per iter, 1.29M per sec
    rand_lookup: 10M  with 16 threads in    0 sec,  1165 nsec per iter, 13.1M per sec
    
    rand_insert: 100M with  1 threads in  165 sec,  1573 nsec per iter , 621K per sec
    rand_insert: 100M with 16 threads in   31 sec,  4849 nsec per iter, 3.15M per sec
    rand_lookup: 100M with  1 threads in   89 sec,   851 nsec per iter, 1.12M per sec
    rand_lookup: 100M with 16 threads in    6 sec,   973 nsec per iter, 15.7M per sec
