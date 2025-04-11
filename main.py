from centroapp import create_app
#run application from init.py
#to run: >python main.py in terminal

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
