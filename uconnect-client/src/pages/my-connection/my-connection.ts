import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { ConnectionService } from "../../services/ConnectionService";
import {ConnectionSummary} from "../../models/connection/ConnectionSummary"
import { AlertController } from 'ionic-angular';


@Component({
  selector: 'page-my-connection',
  templateUrl: 'my-connection.html',
  providers: [ConnectionService]
})
export class MyConnectionPage {
	listItems: ConnectionSummary[];

  constructor(public navCtrl: NavController, public navParams: NavParams, private connectionService: ConnectionService, public alertCtrl: AlertController) {}

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
    console.log('ionViewWillEnter MyConnectionPage load start');
  }
  private handleError(error: any): Promise<any> {
    console.error('An error occurred', error); // for demo purposes only
    return Promise.reject(error.message || error);
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
