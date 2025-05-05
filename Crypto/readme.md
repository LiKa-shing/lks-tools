### 一个简单的加解密工具  
#### 0. 创建环境
```bash
conda env create -f environment.yml
conda activate lks-crypto
```

#### 1. 生成密钥对
```bash
# 生成无密码保护的密钥
python main.py genkeys --private my_private.pem --public my_public.pem

# 生成带密码的密钥
python main.py genkeys --private protected.pem --password "strong_password"
```

#### 2. 加密文件
```bash
python main.py encrypt \
  -i sensitive_data.rar \
  -o encrypted_data.bin \
  -k my_public.pem
```

#### 3. 解密文件
```bash
# 无密码私钥
python main.py decrypt \
  -i encrypted_data.bin \
  -o decrypted.rar \
  -k my_private.pem

# 有密码私钥
python main.py decrypt \
  -i encrypted_data.bin \
  -o decrypted.rar \
  -k protected.pem \
  -p "strong_password"
```


---
| 特性                  | 实现方式                     | 安全收益                     |
|-----------------------|----------------------------|----------------------------|
| 密钥复用              | RSA密钥预先生成长期使用      | 减少密钥管理成本             |
| 前向保密              | 每次加密使用不同AES密钥      | 单个AES密钥泄露不影响历史数据 |
| 抗重放攻击            | 每次随机生成IV              | 防止密文重复被利用           |
| 安全存储              | AES密钥用RSA加密后存储       | 确保只有私钥持有者能解密      |