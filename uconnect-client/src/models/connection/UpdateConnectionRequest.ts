import { MainArg } from "../MainArg";
import { Auth } from "../connection/Auth";
import { Connections } from "./Connections";


export class UpdateConnectionRequest extends MainArg {
  constructor(public Connections:  Array<Connections>, public Auth: Auth) {
	super();

  }
}
