import { MainArg } from "../MainArg";
import { ScheduleDetails } from "./ScheduleDetails";
import { Invitee } from "./Invitee";
import { Repeat } from "./Repeat";
import { Auth } from "../connection/Auth";

export class CreateScheduleData extends MainArg {
  constructor(public ScheduleDetails: ScheduleDetails, public Invitee: Invitee[], public ShareWith: String[], public Tasks: String[], public WaitList: String[], public Repeat: Repeat, public Auth: Auth) {

  super();
  }
}		