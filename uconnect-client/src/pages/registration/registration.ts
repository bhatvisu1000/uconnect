import { Component } from '@angular/core';
import { NgForm } from "@angular/forms";
import { NavController, NavParams } from 'ionic-angular';

import {Member} from "../../models/member/Member"
import { RegistrationService } from "../../services/RegistrationService";
import { MyTabsPage } from '../my-tabs/my-tabs';

@Component({
  selector: 'page-registration',
  templateUrl: 'registration.html'
})

export class RegistrationPage {

  constructor(public navCtrl: NavController, private registrationService: RegistrationService) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad RegistrationPage');
  }

  

  onAddMember(form: NgForm) {
    console.log('before create Member RegistrationPage');
    this.registrationService.createMember(form.value.userId, form.value.password, form.value.firstName, form.value.lastName, form.value.zipCode);
    console.log('before submit RegistrationPage');
    this.registrationService.submitMember(this);
    console.log('before after RegistrationPage');
    this.navCtrl.push(MyTabsPage);
  }
}
