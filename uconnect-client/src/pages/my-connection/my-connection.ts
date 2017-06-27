import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { Storage } from '@ionic/storage';
import {HttpService} from "../../services/HttpService"

import { ConnectionService } from "../../services/ConnectionService";
import {ConnectionSummary} from "../../models/connection/ConnectionSummary"
import { AlertController } from 'ionic-angular';
import {ResponseReceived} from "../../models/ResponseReceived"
import {MyResponse} from "../../models/MyResponse"

import {AuthResponse} from "../../models/response/AuthResponse"

import { AuthService } from "../../services/AuthService";

@Component({
  selector: 'page-my-connection',
  templateUrl: 'my-connection.html',
  providers: [ConnectionService]
})
export class MyConnectionPage {
	listItems: ConnectionSummary[];
  public responseReceived: ResponseReceived;
  public authResponse: AuthResponse;

  constructor(public navCtrl: NavController, public navParams: NavParams, private connectionService: ConnectionService, public alertCtrl: AlertController, public authService: AuthService, public storage: Storage, public httpService: HttpService) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad MyConnectionPage load start');
    
    /*this.authResponse = this.storage.get('AuthResponse');*/
    
    this.loadConnectionData();
	  console.log('ionViewDidLoad MyConnectionPage load end');
    
  }

  loadConnectionData(){
    this.responseReceived = this.authService.responseReceived;
    /*tthis.connectionService.createRequest()*/

  }
  ionViewWillEnter() {
      
    console.log('this.responseReceived ' + this.responseReceived);
  }

  
  
  getItems() {
    let alert = this.alertCtrl.create({
      title: 'New Friend!',
      message: 'Your friend, Obi wan Kenobi, just approved your friend request!',
      buttons: ['Ok']
    });
    alert.present()
  }

  removeItem(){
    let alert = this.alertCtrl.create({
      title: 'New Friend!',
      message: 'Your friend, Obi wan Kenobi, just approved your friend request!',
      buttons: ['Ok']
    });
    alert.present()
  }

  updateResults() {
  let alert = this.alertCtrl.create({
      title: 'New Friend!',
      message: 'Your friend, Obi wan Kenobi, just approved your friend request!',
      buttons: ['Ok']
    });
    alert.present()
    
  }

}
