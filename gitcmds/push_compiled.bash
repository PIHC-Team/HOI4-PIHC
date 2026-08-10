git checkout --orphan latest_branch
source version.bash
git rm -r .
git add --all
git commit -am "$VERSION"
git branch -D main
git branch -m main
git push -f origin main
echo "PIHC $VERSION compiled and force pushed to GitHub"
