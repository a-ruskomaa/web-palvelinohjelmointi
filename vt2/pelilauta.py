# -*- coding: utf-8 -*-

from typing import Callable, Tuple, Type
from flask import Flask, request, render_template, make_response
from flask.helpers import url_for
from werkzeug.datastructures import MultiDict
from wtforms import HiddenField, StringField, validators, ValidationError
from wtforms.fields.html5 import IntegerField as HTML5IntegerField
from flask_wtf_polyglot import PolyglotForm
import os
import urllib.request
import urllib.parse
import urllib.error
import json
import logging

DATA_URL = 'https://europe-west1-ties4080.cloudfunctions.net/vt2_taso1'

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['WTF_CSRF_ENABLED'] = False

# logging.basicConfig(filename=os.path.abspath('../../../../logs/flask.log'),level=logging.DEBUG)
# logging.getLogger().setLevel(logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def handle():
    # Ladataan asetukset (min, max, first, balls)
    try:
        # Jos asetukset löytyvät pyynnöstä, validoidaan ne
        arg_settings = request.args.get('settings', "", type=str)
        settings = validate_settings(arg_settings)
    except (ValueError, ValidationError, KeyError, TypeError) as e:
        # Asetusten puuttuessa tai virheen sattuessa alustetaan asetukset
        logging.debug(e)
        logging.debug("initializing settings")
        settings = initialize_settings()

    # Luodaan lomake, koon rajat asetetaan ladattujen asetusten mukaan
    next_mode = request.args.get('next_mode')
    form = create_form(min=settings['min'], max=settings['max'],
                           def_settings=json.dumps(settings, separators=(',', ':')))
    
    try:
        # Validoidaan lomakkeen sisältö, virhe saa aikaan tilan nollautumisen
        if request.args.get('settings') and form.validate():
            logging.debug("form valid")
            # Lomakkeen kentät on validoitu, haetaan kenttien sisältö muistiin
            user_settings = get_user_settings(request.args)

            # Ladataan pelilaudan tila
            arg_board = request.args.get('board', type=str)
            arg_state = request.args.get('state', type=str)

            # Jos lautaa tai tilaa ei ole määritelty, alustetaan molemmat
            if not (arg_board and arg_state) or next_mode == 'init':
                logging.debug("initializing...")
                state = initialize_state()
                board = initialize_board(user_settings['x'], settings)
                # Tallennetaan tila lomakkeen piilokenttiin
                form.state.data = json.dumps(state, separators=(',', ':'))
                form.board.data = json.dumps(board, separators=(',', ':'))
            # Jos lauta ja tila löytyivät pyynnöstä, validoidaan ne
            else:
                logging.debug("validating...")
                board = validate_board(arg_board, user_settings)
                state = validate_state(arg_state, next_mode, user_settings['x'])

            # Jos on painettu peruutuspainiketta, peruttetaan edellinen poisto
            if next_mode == 'undo':
                logging.debug("undoing...")
                undo_delete(board, state)
                cancel_move(board, state)
                # Tallennetaan uusi tila lomakkeen piilokenttiin
                form.state.data = json.dumps(state, separators=(',', ':'))
                form.board.data = json.dumps(board, separators=(',', ':'))
                state['mode'] = 'delete'

            # Jos on vaihdettu poistotila, keskeytetään mahdollinen siirto
            elif next_mode == 'delete':
                cancel_move(board, state)
                # Tallennetaan uusi tila lomakkeen piilokenttiin
                form.state.data = json.dumps(state, separators=(',', ':'))
                form.board.data = json.dumps(board, separators=(',', ':'))
        else:
            logging.debug("no settings loaded or invalid form:")
            logging.debug(form.errors)
            raise ValidationError

    # Virheen sattuessa nollataan tila
    except (ValueError, ValidationError, KeyError, TypeError) as e:
        user_settings = {}
        board = None
        state = None
        form.state.data = None
        form.board.data = None

    # Luodaan uuden url:n luova funktio sulkeuman avulla, jotta templateen ei tarvitse välittää turhia parametreja
    url_creator = get_url_creator(board, settings, state, user_settings)

    # Valitaan ruudukon pohjavärit asetusten mukaan
    colors = get_color_classes(settings)

    # Renderöidään template ja palautetaan vastauksena
    resp = make_response(render_template("index.xhtml", form=form, board=board,
                                         colors=colors, url_creator=url_creator, state=state, get_img_url=get_img_url, x=str(user_settings.get('x', 1))))
    resp.headers['Content-type'] = 'application/xhtml+xml;charset=UTF-8'
    return resp


######### SETTINGS #########


def initialize_settings() -> dict:
    """Alustaa pelin asetukset joko lataamalla ne palvelimelta tai virheen sattuessa oletusasetuksista"""
    try:
        # Ladataan uudet asetukset
        settings = None
        with urllib.request.urlopen(DATA_URL) as response:
            logging.debug("Loading remote settings")
            settings = json.load(response)
    except urllib.error.URLError:
        # Jos palvelin ei vastaa tms.

        logging.debug("Error, loading fallback settings")
        settings = {
            "min": 8,
            "max": 16,
            "first": "black",
            "balls": "bottom-to-top"
        }

    return settings


def validate_settings(settings: str) -> dict:
    """Validoi asetukset ettei ohjelma kaadu esim. url:n peukaloinnin seurauksena"""
    settings = json.loads(settings)
    
    if not (settings['first'] == 'black' or settings['first'] == 'white'):
        logging.debug("Invalid settings: first")
        raise ValidationError
    if not (settings['balls'] == 'top-to-bottom' or settings['balls'] == 'bottom-to-top'):
        logging.debug("Invalid settings: balls")
        raise ValidationError
    if not (settings['min'] and settings['max']):
        logging.debug("Invalid settings: min or max")
        raise ValidationError

    return settings


def get_user_settings(args: MultiDict) -> dict:
    """Hakee pyynnön argumenteista käyttäjän asetukset. Tekee argumenteille tyyppimuunnokset.
    Mahdolliset virheet jäävät kutsujan käsiteltäviksi."""
    return {
        'x': args.get('x', type=int),
        'pelaaja1': args.get('pelaaja1', type=str),
        'pelaaja2': args.get('pelaaja2', type=str)}


######### STATE #########


def initialize_board(size, settings) -> list:
    """Alustaa pelilaudan. Luo määrätyn kokoisen n x n ruudukon ja asettaa nappulat asetusten mukaisesti"""
    if settings['balls'] == 'top-to-bottom':
        board = [[1 if row == column else 0 for row in range(
            size)] for column in range(size)]
    else:
        board = [[1 if row == size - column -
                  1 else 0 for row in range(size)] for column in range(size)]
    return board


def validate_board(arg_board: str, user_settings: dict) -> list:
    """Validoi pelilaudan ettei ohjelma kaadu esim. url:n peukaloinnin seurauksena"""
    logging.debug("validating board:")
    board = json.loads(arg_board)
    # logging.debug([[col for col in row] for row in board])
    if len(board) != user_settings['x']:
        logging.debug(len(board))
        logging.debug(f"invalid board rows: {len(board)}")
        raise ValidationError
    for row in board:
        logging.debug(row)
        logging.debug(len(board))
        if len(row) != user_settings['x']:
            logging.debug(f"invalid board cols: {len(row)}")
            raise ValidationError
        for col in row:
            if not (col == 0 or col == 1 or col == 2 or col == 3):
                logging.debug(f"invalid cell content: {col}")
                raise ValidationError
    return board


def initialize_state() -> dict:
    """Alustaa pelin tilan. Ohjelma pitää muistissa valitun moodin, edellisen poistetun nappulan sijainnin
    sekä siirron lähtöruudun ja siirrettävän nappulan värin."""
    return {
        'mode': 'delete',
        'del_r': -1,
        'del_c': -1,
        'move_r': -1,
        'move_c': -1,
        'move_color': 0
    }


def validate_state(arg_state: str, next_mode: str, x: int) -> dict:
    """Validoi pelin tilan ettei ohjelma kaadu esim. url:n peukaloinnin seurauksena"""
    state = json.loads(arg_state)

    # Vaihdetaan moodi, mikäli pyynnön argumenteissa oli uusi moodi
    # TODO tämä voisi olla funktion ulkopuolella...
    if next_mode:
        state['mode'] = next_mode

    mode = state['mode']
    if not (mode == 'delete' or mode == 'move' or mode == 'undo'):
        logging.debug(f"Invalid mode: {mode}")
        raise ValidationError

    del_r = state['del_r']
    if del_r < -1 or del_r >= x:
        logging.debug(f"Invalid deleted: {del_r}")
        raise ValidationError

    del_c = state['del_c']
    if del_c < -1 or del_c >= x:
        logging.debug(f"Invalid deleted: {del_c}")
        raise ValidationError

    if (del_c == -1 and del_r != -1) or (del_r == -1 and del_c != -1):
        logging.debug(f"Invalid deleted: {del_r} {del_c}")
        raise ValidationError

    move_r = state['move_r']
    if move_r < -1 or move_r >= x:
        logging.debug(f"Invalid move: {move_r}")
        raise ValidationError

    move_c = state['move_c']
    if move_c < -1 or move_c >= x:
        logging.debug(f"Invalid move: {move_c}")
        raise ValidationError
    
    if (move_c == -1 and move_r != -1) or (move_r == -1 and move_c != -1):
        logging.debug(f"Invalid deleted: {move_r} {move_c}")
        raise ValidationError

    move_color = state['move_color']
    if not (0 <= move_color <= 2):
        logging.debug(f"Invalid move_color: {move_color}")
        raise ValidationError

    return state


######### URL CREATION #########


def get_url_creator(board: list, settings: dict, state: dict, user_settings: dict) -> Callable[[int, int], str]:
    """Funktio luo sulkeuman, jonka avulla argumentteina annetut muuttujat pysyvät
    palautettavan funktion kontekstissa. Palautettava funktio ottaa argumentteinaan
    vain rivi- ja sarakenumeron, joka selkeyttää Jinjan pohjaa."""

    def create_next_url(r: int, c: int):
        """Funktio luo jokaista sallittua seuraavaa tilaa vastaavan url-osoitteen, jotka
        tallennetaan html-pohjassa pelilaudan nappuloihin liitettyjen linkkien osoitteiksi."""
        next_board, next_state = create_next_state(r, c, board, state)
        url_string = urllib.parse.urlencode({'board': json.dumps(next_board, separators=(',', ':')),
                                             'state': json.dumps(next_state, separators=(',', ':')),
                                             'settings': json.dumps(settings, separators=(',', ':')),
                                             **user_settings})
        return url_string

    return create_next_url


######### HELPER FUNCTIONS #########


def create_form(min: int, max: int, def_settings: str, ) -> PolyglotForm:
    """Luo lomakkeen."""
    class NewBoardForm(PolyglotForm):
        x = HTML5IntegerField('Laudan koko', default=min, validators=[validators.InputRequired(message='Syötä arvo!'
        ), validators.NumberRange(min=min, max=max, message="Syöttämäsi arvo ei kelpaa")])
        pelaaja1 = StringField('Pelaaja 1', validators=[validators.InputRequired(message='Syötä arvo!'
        ), validators.Length(min=2, message="Liian lyhyt nimi")])
        pelaaja2 = StringField('Pelaaja 2', validators=[validators.InputRequired(message='Syötä arvo!'
        ), validators.Length(min=2, message="Liian lyhyt nimi")])
        settings = HiddenField(default=def_settings)
        board = HiddenField()
        state = HiddenField()

    form = NewBoardForm(request.args)

    return form


def get_color_classes(settings: MultiDict) -> Tuple[str, str]:
    """Asettaa palauttamiinsa muuttujiin arvoksi 'black' tai 'white' sen
    perusteella mikä on asetuksissa määritelty ensimmäisen ruudun väriksi."""
    even = settings.get('first', 'black')
    odd = 'white' if even == 'black' else 'black'

    return (even, odd)


def cancel_move(board: list, state: dict):
    """Keskeyttää aloitetun siirron muuttamalla siirrettävän nappulan värin takaisin
    aiemmaksi väriksi ja nollaamalla siirron lähtöruudun arvon."""
    move_r = state['move_r']
    move_c = state['move_c']
    move_color = state['move_color']

    # Nollataan tarvittaessa siirron lähtöruudut
    if not (move_r == -1 and move_c == -1):
        board[move_r][move_c] = move_color
        state['move_r'] = -1
        state['move_c'] = -1
        state['move_color'] = 0


def undo_delete(board: list, state: dict):
    """Peruuttaa edellisen poiston. Palauttaa punaisen nappulan ruutuun josta edellinen poisto on tehty."""
    # Spesifikaatio ei kerro, mitä pitää tehdä jos aiemmin poistettu nappula halutaan palauttaa, mutta
    # ruudussa on jo uusi nappula. Nyt vanha nappula korvataan punaisella.
    del_r = state['del_r']
    del_c = state['del_c']
    if del_r == -1 or del_c == -1:
        return
    board[del_r][del_c] = 2
    state['del_r'] = -1
    state['del_c'] = -1


def create_next_state(r: int, c: int, board: list, state: dict) -> Tuple[list, dict]:
    """Laskee jokaiselle ruudulle tilan, joka seuraisi kyseisen ruudun valinnasta pelilaudalla.
    Tilaan vaikuttavat ruudun nykyinen arvo sekä valittu moodi."""
    # Luodaan kopiot edellisestä tilasta selkeyttämään koodia ja ehkäisemään virheitä
    next_board = [row[:] for row in board]
    next_state = state.copy()

    # Haetaan nykyinen tila muuttujiin
    mode = state['mode']
    move_r = state['move_r']
    move_c = state['move_c']
    move_color = state['move_color']

    # Jos on valittu poistotila, saisi ruudun valitseminen nappulan poistumaan
    if mode == 'delete':
        # Asetetaan ruudun seuraavaksi arvoksi nolla
        next_board[r][c] = 0
        # Jos ruutu ei ollut tyhjä, merkitään muistiin mistä poisto tapahtui 
        if board[r][c] != 0:
            next_state['del_r'] = r
            next_state['del_c'] = c

    # Jos on valittu siirtotila, saisi ruudun valitseminen aikaan siirron alun tai lopetuksen
    elif mode == 'move':
        # Jos klikattu ei-tyhjää ruutua
        if board[r][c] != 0:
            # Jos siirto on jo käynnissä, kumotaan se
            if not (move_r == -1 and move_c == -1):
                next_board[move_r][move_c] = move_color
            # Valitaan nappula siirrettäväksi, tallennetaan nykyinen väri
            next_state['move_r'] = r
            next_state['move_c'] = c
            next_state['move_color'] = board[r][c]
            # Vaihdetaan seuraavaan tilaan väriksi 3 (vihreä)
            next_board[r][c] = 3

        # Jos klikattu ruutu on tyhjä ja siirto on jo käynnissä
        elif not (move_r == -1 and move_c == -1):
            # Siirretään uuteen ruutuun ja nollataan siirtotila
            next_board[r][c] = move_color
            next_board[move_r][move_c] = 0
            next_state['move_color'] = 0
            next_state['move_r'] = -1
            next_state['move_c'] = -1

    return next_board, next_state


def get_img_url(cell_data: int) -> str:
    """Luo osoitteen pelinappulan kuvaan ruutuun asetetun arvon perusteella"""
    if cell_data == 1:
        return url_for('static', filename='blue.svg')
    elif cell_data == 2:
        return url_for('static', filename='red.svg')
    elif cell_data == 3:
        return url_for('static', filename='green.svg')
    else:
        return None


# Route responsiivisen css:n luomista varten. CSS luodaan templatesta,
# jossa muuttuja x korvataan pelilaudan yhdellä sivulla olevien ruutujen
# määrällä.
@app.route('/<x>/style.css', methods=['GET'])
def css_generator(x):
    x = int(x)
    resp = make_response(render_template("style.css", x=x))
    resp.headers['Content-type'] = "text/css; charset=UTF-8"
    return resp
