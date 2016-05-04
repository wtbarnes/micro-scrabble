from micro_scrabble import app,db
db.create_all()
app.run(debug=True)
