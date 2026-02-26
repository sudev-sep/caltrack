import { HttpInterceptorFn } from '@angular/common/http';
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Inject the platform ID to safely check for SSR (Server-Side Rendering)
  const platformId = inject(PLATFORM_ID);

  // Only try to get the token if we are in the browser
  if (isPlatformBrowser(platformId)) {
    const token = localStorage.getItem('token');

    if (token) {
      // Clone the request and add the Authorization header
      const clonedReq = req.clone({
        setHeaders: {
          Authorization: `Token ${token}`
        }
      });
      
      // Send the modified request to the next handler
      return next(clonedReq);
    }
  }

  // If no token or running on the server, send the original request
  return next(req);
};