declare module 'logdna-winston' {
  import { TransportStream } from 'winston';

  interface LogdnaWinstonOptions {
    key: string;
    app?: string;
    env?: string;
    hostname?: string;
    ip?: string;
    mac?: string;
    level?: string;
    indexMeta?: boolean;
    handleExceptions?: boolean;
  }

  class LogdnaWinston extends TransportStream {
    constructor(options: LogdnaWinstonOptions);
  }

  export = LogdnaWinston;
} 