declare module 'react-query' {
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

  export interface UseQueryOptions {
    keepPreviousData?: boolean;
    enabled?: boolean;
    retry?: boolean | number;
    refetchOnMount?: boolean;
    refetchOnWindowFocus?: boolean;
  }

  export interface UseQueryResult<T = any> {
    data?: T;
    isLoading: boolean;
    isError: boolean;
    error?: Error | null;
    refetch: () => Promise<void>;
  }

  export function useQuery<T = any>(
    queryKey: any[],
    queryFn: () => Promise<T> | T,
    options?: UseQueryOptions
  ): UseQueryResult<T>;

  export const QueryClient: QueryClient;
  export const QueryClientProvider: QueryClientProvider;
  
  interface QueryFunctionContext {
    queryKey: unknown[];
    signal?: AbortSignal;
  }
}
