"use client";

import {Amplify} from 'aws-amplify';
import {Authenticator} from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import outputs from '../amplify_outputs.json';

Amplify.configure(outputs, {ssr: true});


export const Providers = ({children}: { children: React.ReactNode }) => {
  return (
    <Authenticator>
      {children}
    </Authenticator>
  );
}
