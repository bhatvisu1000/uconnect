import { ConnectionSummary } from "./ConnectionSummary";
export class ConnectionDetailEntity {
  constructor(public ConnectionSummary: ConnectionSummary, public Prefix: string) {}
}