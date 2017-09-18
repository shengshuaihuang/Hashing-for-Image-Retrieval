# Hashing for Image Retrieval

Implement of hashing methods for image retrieval in Python and this version use the DPLM method:
```
    Shen F, Zhou X, Yang Y, et al. A fast optimization method for general binary code learning  
    IEEE Transactions on Image Processing, 2016, 25(12): 5610-5621.
```
In further version, I will add more methods, especially end-to-end framework methods. If you have any question, you can ask me through Issues. 


## Getting started
1. Configure Caffe enviroment, you can refer to this [document](http://caffe.berkeleyvision.org/installation.html). Then replace the caffe_root to your own in app.py line 12.
2. Configure MySql enviroment.
3. Import the hashing binary code to your own database, the database named irs_sun397.sql is in folder fold. The details are in [Database](#database).
4. Modify the database configuration in utils/utils.py line 99 and line 121.
5. Download the hashing model from [here]() and place in caffe_model folder.
6. Run app.py using command, then open browser to browse http://127.0.0.1:5000.
```shell
    python app.py
```

## Dataset and deep feature
I extract the SUN397 dataset VGG16's fc7' feature via deep learning framework Caffe. You can click [here](http://groups.csail.mit.edu/vision/SUN/) where offer details about SUN397 dataset and download [link](http://vision.princeton.edu/projects/2010/SUN/SUN397.tar.gz). The VGG16 pre-trained model can be download from [here](https://gist.github.com/ksimonyan/211839e770f7b538e2d8). 
[comment]:The raw features can be download from [here]() and code is xxx

## Hashing binary code
After some pre-process(center and normlize), 4096-d feature transformed into 128-bit hashing binary code by using hashing method. The model can be download from [here]().

## <span id="database">Database</span>
The hashing binary code are stored in the database with mysql. The database is named irs_sun397.sql and the table img construction is bellow: 

| Field  |      Type    | Null  | Key | Default |      Extra     |
| ------ |:-------------| -----:| --- |:-------:|:--------------:|
| id     | int(11)      | NO    | PRI | NULL    | auto_increment |
| path   | varchar(150) | YES   |     | NULL    |                |
| code_1 | bigint(20)   | YES   |     | NULL    |                |
| code_2 | bigint(20)   | YES   |     | NULL    |                |
| code_3 | bigint(20)   | YES   |     | NULL    |                |
| code_4 | bigint(20)   | YES   |     | NULL    |                |

A detailed data is as follows

|id    | path      | code_1     | code_2    | code_3     | code_4  |
|------|-----------|------------|-----------|------------|---------|
| 10000 | /SUN397/m/manufactured_home/sun_bwnvkpvdgnxhkjst.jpg | 4076301309 |917904382 | 1211050903 | 2286664558 |

The database can be found in folder DB and imported to your own database using command:
```sql
    source irs_sun397.sql
```

A hamming distance function has to be created in order to retrieval simililar images with hashing binary code. 

```sql
CREATE FUNCTION HAMMINGDISTANCE(
  A0 BIGINT, A1 BIGINT, A2 BIGINT, A3 BIGINT, 
  B0 BIGINT, B1 BIGINT, B2 BIGINT, B3 BIGINT
)
RETURNS INT DETERMINISTIC
RETURN 
  BIT_COUNT(A0 ^ B0) +
  BIT_COUNT(A1 ^ B1) +
  BIT_COUNT(A2 ^ B2) +
  BIT_COUNT(A3 ^ B3);
```

