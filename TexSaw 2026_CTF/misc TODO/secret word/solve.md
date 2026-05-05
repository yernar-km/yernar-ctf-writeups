.docx файлы внутри являются обычными ZIP-архивами. Распаковав challenge.docx как ZIP, среди стандартных файлов Word обнаружился посторонний secret.txt с base64-строкой. Декодировали — получили флаг
bashunzip challenge.docx
cat secret.txt | base64 -d
Flag: texsaw{surpr1se!_w0rd_f1les_ar3_z1p_4rchives_60709013771}