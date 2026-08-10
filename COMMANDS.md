# 编译工程

快速（图片会缓存，即更换图片可能不会变化）：

```bash
python v0.2.3.py
```

完整：

```bash
python v0.2.3.py -f
```


# 新建分支

（每次合并后修改前）

```bash
git checkout -b <你自己随便起名>
```

例如开发星光国家，就一直沿用同一个名字starlight，只要避免与主分支main冲突就行。

# 保存修改

```bash
git add --all
git commit -m "<随便写点啥描述你改了啥，或者偷懒直接写个upd>"
git push -u
```

原理是将本地这段时间的修改，保存在你所在的分支上（即上一步创建的starlight分支）。

# 同步修改

（这一步合并冲突可能比较复杂，建议交给Tali）

```bash
git checkout main # 切换到主分支
git pull # 同步别人（Tali）的修改
git merge <你的分支名, 例如starlight> # 合并你的修改
# 手动解决冲突
git add --all # 添加修改
git commit -m "<随便写点啥描述你改了啥，或者偷懒直接写个upd>"
git push -u # 推送到主分支
git branch -D <你的分支名, 例如starlight> # 删除已经合并完的分支
git checkout -b <你的分支名, 例如starlight> # 重新建立分支
```
TEST