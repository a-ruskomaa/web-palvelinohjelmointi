import React, { PureComponent } from 'react'


class Valikko extends PureComponent {
    constructor(props) {
        super(props);
      }

      render() {
          const { paikkakunta, handleValikkoSelect, handleValikkoRemove } = this.props
          
        return (
            <div className="valikko">
                <div onClick={(e) => handleValikkoSelect(paikkakunta, 1, e)}>Valitse paikkaan 1</div>
                <div onClick={(e) => handleValikkoSelect(paikkakunta, 2, e)}>Valitse paikkaan 2</div>
                <div onClick={(e) => handleValikkoSelect(paikkakunta, 3, e)}>Valitse paikkaan 3</div>
                <div onClick={(e) => handleValikkoRemove(paikkakunta, e)}>Poista paikkakunta</div>
            </div>
        )
      }
}

export default Valikko