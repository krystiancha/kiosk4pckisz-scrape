all:
	rm -rf tmp/
	mkdir tmp
	rm -rf package.zip
	cp -r kiosk4pckisz_scrape/ tmp/
	cp -r venv/lib/python3.7/site-packages/* tmp/
	cd tmp && zip -r ../package.zip ./*
	rm -rf tmp/
	aws lambda update-function-code --function-name kiosk4pckisz-scrape --zip-file fileb://package.zip
