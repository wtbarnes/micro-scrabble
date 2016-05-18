from micro_scrabble import app,db
import argparse
parser = argparse.ArgumentParser(description="Startup Flask scrabble server")
parser.add_argument('--deploy',action='store_true')
args = parser.parse_args()
db.create_all()
if args.deploy:
    app.run(host='0.0.0.0')
else:
    app.run(debug=True)
