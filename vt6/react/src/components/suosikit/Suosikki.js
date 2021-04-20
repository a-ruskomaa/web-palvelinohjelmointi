import React, { PureComponent } from 'react'

class Suosikki extends PureComponent {
    constructor(props) {
        super(props);
      }

      render() {
        const { paikkakunta, avattu, handleSuosikkiClick } = this.props;
        return (
          <div className={`suosikki ${avattu ? "avattu" : undefined}`} onClick={() => handleSuosikkiClick(paikkakunta)}>{paikkakunta}</div>
        )
      }
}

export default Suosikki