# RH Risk Managment

This open source project was developed as a a tool to handle automated risk managment, via dynamic trailing stop. This was developed because robinhood app currently does not implement such functionalities. Please feel free to fork and contribute as you like(see guidlines before proceeding pull request)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

To use this module, please install the following


```
keyring [version > 10.1]
python [version > 3.3]

if using ubuntu 
please install 
genome-keyring as specifies
```
### Starting
Paramters includes
```
-s symbole [4 character string stock symbol]
-e equity [floating point dollar amount to load into app]
-l lose  [floating point dollar amount for our risk(trailing stop amount)]
-w win  [floating point dollar amount for our exit strategy(to exit a stock movemnt on upside)]
-p premarket [boolean 'T'/'F' to turn on scheduled run when market opens defaults to NOW]
```

#example usage
assuming you want the module to track 740 dollars of your equity
- when the price drops to a point where you lose $50 automate limit sell
- when the price rises to a point where you lock in $100 produce a limit sell
- lower pointer will trail the price movement upwards, and attempt to lock your win amount
for example if the price moves up to a point the portfolio is making $100 set a trigger
to sell if the price moves any lower, however if the price continues upward, 
keep trailing.
```
~$: riskmanagment AMD 740 50 100 

```

## Built With

* [Robinhood Endpoints](https://github.com/sanko/Robinhood) - The web framework used

## Contributing

Please read [ContributingGuildlines.md](https://github.com/RedKlouds/RH-Risk-Managment/blob/master/ContributingGuildlines.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [Git](http://Git.org/) for versioning. 

## Authors

* **Danny Ly** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
