import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage';


@Injectable()
export class SQLStorageService {

constructor(private storage: Storage) {}

	put(key: string, value: string): void  {
		  
          this.storage.set(key, value);
	}

	/*get(key: string): string  {
		  
          this.storage.get(key).then((key) => {
			  console.log('Me: Hey, ' + name + '! You have a very nice name.');
			  console.log('You: Thanks! I got it for my birthday.');
			});
          return this.storage.get(key);
	}*/
}