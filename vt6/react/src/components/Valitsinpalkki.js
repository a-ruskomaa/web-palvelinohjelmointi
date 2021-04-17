import React, { PureComponent } from "react";
import Valitsin from './Valitsin'

class Valitsinpalkki extends PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        const {paikkakuntaValinnat, paikkakunnat, onValitsinChange, onValitsinClick} = this.props;
        return (
            <div className="valitsinpalkki">
                <h3>Valitut paikkakunnat</h3>
                <Valitsin
                    id={1}
                    valittu={paikkakuntaValinnat[0]}
                    paikkakunnat={paikkakunnat}
                    onValitsinClick={onValitsinClick}
                    onValitsinChange={onValitsinChange}/>
                <Valitsin
                    id={2}
                    valittu={paikkakuntaValinnat[1]}
                    paikkakunnat={paikkakunnat}
                    onValitsinClick={onValitsinClick}
                    onValitsinChange={onValitsinChange}/>
                <Valitsin
                    id={3}
                    valittu={paikkakuntaValinnat[2]}
                    paikkakunnat={paikkakunnat}
                    onValitsinClick={onValitsinClick}
                    onValitsinChange={onValitsinChange}/>
                <p>Kaksoisklikkaa karttaa valitaksesi sijainnin</p>
            </div>
        );
    }
}

export default Valitsinpalkki

