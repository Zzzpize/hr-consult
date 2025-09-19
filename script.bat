git init
git remote add origin https://github.com/Zzzpize/hr-consult
git branch -M mlbranch1
python -m venv --upgrade-deps venv
Set-ExecutionPolicy RemoteSigned
venv\Scripts\activate
echo venv > .gitignore
git add .
git commit -m "Initial commit"
git push -u origin mlbranch1