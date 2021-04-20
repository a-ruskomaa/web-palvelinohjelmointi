import React, { PureComponent } from 'react'
import Suosikki from './Suosikki'
import Valikko from './Valikko'

class Suosikit extends PureComponent {
    constructor(props) {
        super(props);
    
        this.state = {
          avattuValikko: null
        }
      }

      handleSuosikkiClick = (paikkakunta) => {
        // Asetetaan klikattu paikkakunta valituksi tai poistetaan valinta jos on klikattu valittua paikkakuntaa
        if (this.state.avattuValikko === paikkakunta) {
          this.setState({avattuValikko: null})
        } else {
          this.setState({avattuValikko: paikkakunta})
        }
      }

      render() {
        const { suosikit, handleValikkoSelect, handleValikkoRemove } = this.props

        const suosikkiElems = suosikit.map(([suosikki, lkm]) => {
          return (<div key={`suosikki_${suosikki}`}>
            <Suosikki paikkakunta={suosikki} handleSuosikkiClick={this.handleSuosikkiClick} />
            {this.state.avattuValikko === suosikki ?
              // Renderöidään valikko suosikkikomponentin alle jos kyseinen paikkakunta on valittuna
              <Valikko
                paikkakunta={suosikki}
                handleValikkoSelect={handleValikkoSelect}
                handleValikkoRemove={handleValikkoRemove}
              /> : null
            }
          </div>)
        })

        return (
          <div className="suosikit">
            <h3>Suosikit</h3>
            {suosikkiElems}
          </div>
        )
      }
}

export default Suosikit