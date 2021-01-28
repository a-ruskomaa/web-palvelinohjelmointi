import vt

if __name__ == '__main__':
    app = vt.create_app()
    # asetetaan debug-moodi päälle. Ei saa pitää päällä tuotantokäytössä
    app.debug = True
    app.env = 'development'
    app.run()
