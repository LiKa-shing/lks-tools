## 
### ---------------
###
### Create: Li Ka-shing
### Date: 2025-4-20
### The First Affiliated Hospital of Xi'an Jiao Tong University
### 2nd version
###
### ---------------
rm(list = ls())

## 创建待安装的R packages向量，下面的内容需要修改成自己需要安装的包名
bioPackages <-c( 
  "ggplot2",
  "corrplot",    # 绘制相关性图形
  "ggrepel",           
  "stringr",     # 处理字符串的包                   
  "FactoMineR",
  "factoextra",  # PCA分析软件
  "limma",
  "edgeR",
  "DESeq2",          # 差异分析的三个软件包
  "clusterProfiler", 
  "org.Hs.eg.db",    # 安装进行GO和Kegg分析的扩展包
  "org.Mm.eg.db",
  "GSEABase",
  "GSVA",             # 安装进行GSEA分析的扩展包
  "pheatmap",
  "tidyverse",
  "rtracklayer",
  "GenomicFeatures",
  "randomForest",
  "caret",
  "e1071",
  "dplyr",
  "ggridges",
  'preprocessCore',
  "ComplexHeatmap",
  "ggthemes",
  "ggprism"
)
#如果能明白这一步是做什么，把括号里的F改为T，否则不要修改
if(F){
  #添加本地代理，根据实际情况修改端口号
  Sys.setenv(http_proxy = "http://127.0.0.1:23333")
  Sys.setenv(https_proxy = "http://127.0.0.1:23333")
}
# 函数用于检测当前网络环境是否为中国大陆网络
# 返回值: TRUE 表示中国大陆网络，FALSE 表示非中国大陆网络
check_china_network <- function() {
  # 引入必要的包
  if (!require("httr")) {
    install.packages("httr")
    library(httr)
  }
  
  # 定义测试用的中国大陆网站列表
  cn_sites <- c(
    "https://www.baidu.com",
    "https://www.qq.com",
    "https://www.taobao.com"
  )
  
  # 定义测试用的国际网站列表
  global_sites <- c(
    "https://www.google.com",
    "https://www.facebook.com",
    "https://www.twitter.com"
  )
  
  # 测试连接函数
  test_connection <- function(url) {
    tryCatch({
      response <- GET(url, timeout(5))
      return(status_code(response) == 200)
    }, error = function(e) {
      return(FALSE)
    })
  }
  
  # 测试中国大陆网站可访问性
  cn_access <- sapply(cn_sites, test_connection)
  cn_score <- mean(cn_access)
  
  # 测试国际网站可访问性
  global_access <- sapply(global_sites, test_connection)
  global_score <- mean(global_access)
  
  # 返回布尔值：当中国网站可访问性高且国际网站可访问性低时返回TRUE
  return(cn_score > 0.5 && global_score < 0.5)
}

# 使用示例
is_china <- check_china_network()
print(is_china)  # 输出 TRUE 或 FALSE
# 自动设置镜像源
if (check_china_network()) {
  message("检测到当前网络在中国大陆，设置国内镜像源...")
  options(BioC_mirror = "https://mirrors.tuna.tsinghua.edu.cn/bioconductor/")
  options("repos" = c(CRAN = "http://mirrors.cloud.tencent.com/CRAN/"))
  options(download.file.method = 'libcurl')
  options(url.method = 'libcurl')
} else {
  message("当前网络不在中国大陆，使用默认镜像源...")
  # 恢复R语言默认源设置
  # 设置默认的CRAN镜像
  options("repos" = c(CRAN = "https://cran.r-project.org"))
  # 设置默认的Bioconductor镜像
  options(BioC_mirror = "https://bioconductor.org")
  # 恢复默认的下载方法
  options(download.file.method = "auto")
  options(url.method = "default")
}

# 检查镜像设置是否正确
message("当前使用的 CRAN 镜像: ", options()$repos)
message("当前使用的 Bioconductor 镜像: ", options()$BioC_mirror)

if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")
#Rtools不能通过常规install.packages()命令进行安装，需要通过installr包进行安装
if (!requireNamespace("installr", quietly = TRUE)) install.packages("installr")
if (!requireNamespace("stringr", quietly = TRUE)) install.packages("stringr")
library(stringr)
library(installr)
install.Rtools()
# 安装devtools管理github上的软件包
if (!requireNamespace("devtools", quietly = TRUE)) install.packages("devtools")
# 提前获取已安装包和 CRAN 包列表
installed <- rownames(installed.packages())
CRANpackages <- rownames(available.packages())

# 创建一个向量存储未能安装的包
missing_packages <- c()

# 检查并安装包
lapply(bioPackages, function(bioPackage) {
  if (!bioPackage %in% installed) {
    if (bioPackage %in% CRANpackages) {
      install.packages(bioPackage)
    } else {
      tryCatch(
        {
          BiocManager::install(bioPackage, suppressUpdates = FALSE, ask = FALSE)
        },
        error = function(e) {
          message(sprintf("无法安装包: %s，原因: %s", bioPackage, e$message))
          missing_packages <<- c(missing_packages, bioPackage)  # 记录未安装的包
        }
      )
    }
  }
})

# 输出未能安装的包
if (length(missing_packages) > 0) {
  message("以下包无法通过 CRAN 或 Bioconductor 安装，请手动检查和安装：")
  print(missing_packages)
}