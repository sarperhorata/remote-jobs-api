declare module '@tanstack/react-query' {
  export interface QueryClient {
    new(options?: any): QueryClient;
    resetQueries: (options?: any) => Promise<void>;
    invalidateQueries: (options?: any) => Promise<void>;
    refetchQueries: (options?: any) => Promise<void>;
    setQueryData: (queryKey: any, updater: any) => void;
  }

  export interface QueryClientProvider {
    (props: { children: React.ReactNode; client: QueryClient }): JSX.Element;
  }

  export const QueryClient: QueryClient;
  export const QueryClientProvider: QueryClientProvider;
}
