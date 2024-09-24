if __name__ == '__main__':
    # print("This is not meant to be run by initialzing flask instance")
    # print("Please use gunicorn -w 4 -b 127.0.0.1:8006 app:app")
    # print("use the any given ip you wish to use")
    # print("change line 179 in route if you wish to change ip and socket")
    # import sys
    # sys.exit()
    from app import app

    app.run(debug=True,host="127.0.0.1", port=8000)


from app import app

