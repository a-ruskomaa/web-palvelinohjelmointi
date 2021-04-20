import React, { PureComponent } from "react";

class Valitsin extends PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        const { id, valittuPaikkakunta, kartallaNaytetaan, paikkakunnat, onValitsinClick, onValitsinChange } = this.props;
        return (
            <select className={kartallaNaytetaan ? "valittu" : undefined}
                name={`valinta${id}`}
                id={`valinta${id}`}
                value={valittuPaikkakunta}
                onClick={(e) => onValitsinClick(e.target.value, id, e)}
                onChange={(e) => onValitsinChange(e.target.value, id, e)}>

                <option value="kartta">Valitse kartalta</option>
                {paikkakunnat.map((pk) => 
                    <option key={`${id}_pk_${pk}`} value={pk}>{pk}</option>
                )}
            </select>
        );
    }
}

export default Valitsin