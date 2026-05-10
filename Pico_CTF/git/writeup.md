нужно работать с коммитами 

проверяем историю ничего нет 

потом подделываем коммит от автора рут 

далее выводи флаг 

PS C:\Users\Stut\Desktop\challenge> git log --author="root:root@picoctf"
PS C:\Users\Stut\Desktop\challenge> git log --all --oneline --graph
* b4df14d (HEAD -> master, origin/master, origin/HEAD) Challenge commit
PS C:\Users\Stut\Desktop\challenge> git log --all --author="root"
PS C:\Users\Stut\Desktop\challenge> echo "some changes" >> flag.txt
PS C:\Users\Stut\Desktop\challenge> git add flag.txt
PS C:\Users\Stut\Desktop\challenge> git commit --author="root <root@picoctf>" -m "Update flag"
[master 1d1582a] Update flag
 Author: root <root@picoctf>
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 flag.txt
PS C:\Users\Stut\Desktop\challenge> git push origin master