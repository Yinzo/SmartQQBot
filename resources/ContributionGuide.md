Contribution Guide（贡献文档）
-----------------------------------

如果你想给SmartQQBot贡献代码，请遵循Github的标准工作流：）

参见：[Github Workflow](https://guides.github.com/introduction/flow/)


除此之外，你需要在对Master分支发起PR之前，进行一次 `rebase` 操作，以保证你的代码是最新的，并和主分支没有冲突。

## Summary

试想发生如下情况：

1. 你Fork了项目
2. 在你添加Commit期间，主分支也向前前进了CommitA，假定你的Commit叫做CommitB.
3. 你对项目Master发起PR
 
 
这时候有两个问题：

1. 你的分支里缺少了CommitA
2. 如果你选择把新的主分支Merge到你的分支，再发起PR，那么，会产生一次额外的“Merge Mater to your-feature-branch”的提交，历史将变得十分难看。

这时候，使用Rebase可以解决这个问题。

## More Detail

具体的操作，可以如下：

```
# Add a new remote, you can customize its name
git remote add pr https://github.com/Yinzo/SmartQQBot.git

# Fetch the newest remote to FETCH_HEAD
git fetch pr master

# Rebase your branch based on master
git checkout your-feature-branch

# In this step, if conflicts detected, you should resolve it 
# and push to your remote repo, then create your PR.
git rebase FETCH_HEAD

# Push your changes to your forked repo
git push origin your-feature-branch

# Now you can create a PR that has no conflicts with master and is fast-forward.
```