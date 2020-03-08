import React, { Component } from 'react';
import Loader from 'react-loader-spinner';
import ProbablyGenetics from './assets/probably-genetics.png';
import EmptyState from './assets/empty_state.png';

const colors = {
  white: '#FFFF',
  black: '#525252',
  grey: '#A09F9F'
};

class FrontEnd extends Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      searchValue: '',
      typingTimeout: null,
      results: []
    };
  }

  search = value => {
    const now = Date.now();

    // clear old timeouts
    if (this.state.typingTimeout) {
      clearTimeout(this.state.typingTimeout);
    }

    // set timeout to trigger search at end of typing
    this.setState({
      searchValue: value,
      lastTextChangeTime: now,
      typingTimeout: setTimeout(() => {
        this.setState({ loading: true });

        // hit django api
        fetch(`api/?q=${value}`)
          .then(res => res.json())
          .then(data => {
            // store results
            this.setState({ results: data.results, loading: false });
          })
          .catch(() => this.setState({ loading: false }));
      }, 1000)
    });
  };

  render() {
    return (
      <div className="container">
        <div className="search-container">
          <div className="logo">
            <img width={100} src={ProbablyGenetics} />
          </div>
          <SearchBar
            value={this.state.searchValue}
            loading={this.state.loading}
            onChange={event => this.search(event.target.value)}
          />
          {this.state.results.length == 0 && (
            <img width={380} src={EmptyState} />
          )}
          {this.state.results.length > 0 &&
            this.state.results.map((result, i) => (
              <Result key={i} {...result} />
            ))}
        </div>
        <style jsx>{`
          .container {
            display: flex;
            flex: 1;
            justify-content: center;
            background-color: ${colors.white};
          }
          .search-container {
            margin-top: 50px;
            align-items: left;
          }
          .logo {
            display: flex;
            flex: 1;
            justify-content: center;
            align-items: center;
            padding-bottom: 25px;
          }
        `}</style>
      </div>
    );
  }
}

const SearchBar = props => {
  return (
    <div className="search-bar">
      <input
        placeholder={'what are your symptoms...'}
        onChange={props.onChange}
        value={props.value}
      />
      {props.loading && (
        <Loader type="TailSpin" color={colors.black} height={20} width={20} />
      )}
      <style jsx>{`
        .search-bar {
          display: flex;
          flex: 1;
          justify-content: space-between;
          align-items: center;
          padding: 0px 10px;
          margin-bottom: 14px;
          width: 360px;
          height: 35px;
          border-radius: 8px;
          box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.43);
          background-color: ${colors.white};
        }
        input {
          font-family: Avenir-Medium;
          font-size: 14px;
          width: 90%;
          border-width: 0px;
          background-color: transparent;
          text-align: left;
          color: ${colors.black};
        }
        input::placeholder {
          color: ${colors.grey};
        }
        input:focus {
          outline: none;
        }
      `}</style>
    </div>
  );
};

const Result = props => {
  const prob = (props.prob * 100).toFixed(2);
  return (
    <a style={{ textDecoration: 'none' }} href={props.link}>
      <div className="search-result">
        <div className="disorder-name">
          <span>{props.disorder}</span>
        </div>
        <div>
          <span className="prob-match">{prob}% match</span>
          <span className="learn-more">learn more</span>
        </div>
      </div>
      <style jsx>{`
        .search-result {
          display: flex;
          flex: 1;
          padding: 5px 10px;
          margin-bottom: 14px;
          width: 360px;
          border-radius: 8px;
          box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.43);
          background-color: ${colors.white};
          align-items: center;
          justify-content: space-between;
        }
        .search-result:hover {
          opacity: 0.6;
        }
        .disorder-name {
          width: 195px;
        }
        span {
          font-family: Avenir-Medium;
          font-size: 14px;
          color: ${colors.black};
        }
        .prob-match {
          font-size: 10px;
          margin-right: 7px;
        }
        .learn-more {
          color: ${colors.grey};
          font-size: 10px;
        }
      `}</style>
    </a>
  );
};

export default FrontEnd;
