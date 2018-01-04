import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { ConnectionService } from "../../services/ConnectionService";
import {Connections} from "../../models/connection/Connections"

@Component({
  selector: 'page-my-connection',
  templateUrl: 'my-connection-details.html',
  providers: [ConnectionService]
})
export class MyConnectionPage {
	listItems: Connections[];

  constructor(public navCtrl: NavController, public navParams: NavParams, private connectionService: ConnectionService) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad MyConnectionPage load start');
    
	 console.log('ionViewDidLoad MyConnectionPage load end');
    
  }
  ionViewWillEnter() {
    console.log('ionViewWillEnter MyConnectionPage load start');
  }
  
  
}
