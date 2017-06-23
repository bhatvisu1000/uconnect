import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { ConnectionService } from "../../services/ConnectionService";
import {ConnectionSummary} from "../../models/connection/ConnectionSummary"
import { AlertController } from 'ionic-angular';
import {ResponseReceived} from "../../models/ResponseReceived"

import { AuthService } from "../../services/AuthService";

@Component({
  selector: 'page-my-connection',
  templateUrl: 'my-connection.html',
  providers: [ConnectionService]
})
export class MyConnectionPage {
	listItems: ConnectionSummary[];
  public responseReceived: ResponseReceived;

  constructor(public navCtrl: NavController, public navParams: NavParams, private connectionService: ConnectionService, public alertCtrl: AlertController, public authService: AuthService) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad MyConnectionPage load start');
    
    
    this.connectionService.fetchList("")
    .subscribe(
                    (list: ConnectionSummary[]) => {
                      console.log('ConnectionSummary List inside');
                      if (list) {
                      	console.log('ConnectionSummary if List inside');
                      	for (let entry of list) {
						    console.log(entry); 
						}
                        this.listItems = list;
                      } else {
                        this.listItems = [];
                      }
                    },
                    error => {
                      console.log('error ' + error.json().error);
                      
                    }
                  );
	console.log('ionViewDidLoad MyConnectionPage load end');
    
  }

  ionViewWillEnter() {
      this.responseReceived = this.authService.responseReceived;
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
