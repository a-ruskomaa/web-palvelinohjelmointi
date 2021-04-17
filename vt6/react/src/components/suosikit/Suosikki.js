import React, { PureComponent } from 'react'

class Suosikki extends PureComponent {
    constructor(props) {
        super(props);
      }

      render() {
        const { paikkakunta, handleSuosikkiClick } = this.props;
        return (
          <div className="suosikki" onClick={() => handleSuosikkiClick(paikkakunta)}>{paikkakunta}</div>
        )
      }
}

export default Suosikki