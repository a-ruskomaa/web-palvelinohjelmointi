import React, { PureComponent } from "react";
import Valitsin from './Valitsin'

class Valitsinpalkki extends PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        const {paikkakuntaValinnat, kartallaNaytetaan, paikkakunnat, onValitsinChange, onValitsinClick} = this.props;
        return (
            <div className="valitsinpalkki">
                <h3>Valitut paikkakunnat</h3>
                <Valitsin
                    id={1}
                    valittuPaikkakunta={paikkakuntaValinnat[0]}
                    kartallaNaytetaan={kartallaNaytetaan === 1}
                    paikkakunnat={paikkakunnat}
                    onValitsinClick={onValitsinClick}
                    onValitsinChange={onValitsinChange}/>
                <Valitsin
                    id={2}
                    valittuPaikkakunta={paikkakuntaValinnat[1]}
                    kartallaNaytetaan={kartallaNaytetaan === 2}
                    paikkakunnat={paikkakunnat}
                    onValitsinClick={onValitsinClick}
                    onValitsinChange={onValitsinChange}/>
                <Valitsin
                    id={3}
                    valittuPaikkakunta={paikkakuntaValinnat[2]}
                    kartallaNaytetaan={kartallaNaytetaan === 3}
                    paikkakunnat={paikkakunnat}
                    onValitsinClick={onValitsinClick}
                    onValitsinChange={onValitsinChange}/>
                <p>Kaksoisklikkaa karttaa valitaksesi sijainnin</p>
            </div>
        );
    }
}

export default Valitsinpalkki

