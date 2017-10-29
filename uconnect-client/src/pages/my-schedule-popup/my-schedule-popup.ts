import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import 'rxjs/add/operator/map';

/*
  Generated class for the MySchedulePopup page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
  selector: 'page-my-schedule',
  templateUrl: 'my-schedule-popup.html'
})
export class MySchedulePopupPage {

  constructor(public navCtrl: NavController, public navParams: NavParams) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad MySchedulePage');
  }
  /*ionViewWillEnter() {
      var url = 'http://api.themoviedb.org/3/search/movie?query=&query=' + encodeURI(movieName) + '&api_key=5fbddf6b517048e25bc3ac1bbeafb919';
      var response = this.http.get(url).map(res => res.json());
      return response;
  }*/


}
