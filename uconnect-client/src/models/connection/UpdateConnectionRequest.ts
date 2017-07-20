import { MainArg } from "../MainArg";
import { Auth } from "../connection/Auth";
import { Connections } from "./Connections";


export class UpdateConnectionRequest extends MainArg {
  constructor(public UpdateConnections:  Array<Connections>, public Auth: Auth) {
	super();

  }
}
