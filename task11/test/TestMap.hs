{-# LANGUAGE ScopedTypeVariables #-}  -- Включаем некоторые расширения компилятора.
import Test.Tasty
import Test.Tasty.HUnit
import Data.Proxy
import Map
import qualified Data.Map.Strict as SMap
import MapInstance
import NaiveList(NaiveList)  -- Импортируем только тип NaiveList, но не его конструкторы Nil/Cons, чтобы не путались с конструкторами NaiveTree.
import NaiveTree

main :: IO ()
main = defaultMain testMap

{-|
  Генерирует группу тестов для конкретной реализации 'Map'
  с определённым именем.

  Мы хотим писать тесты один раз для всех возможных реализаций 'Map'.
  В чистом Haskell нам может помочь параметрический полиморфизм,
  но для этого нужно, чтобы в сигнатуре функции присутствовал
  тип из класса 'Map', который мы хотим протестировать.

  Специально для этих целей существует обёртка 'Data.Proxy', он
  позволяет передавать в функции даже типы высшего порядка.
-}
mapTests :: Map m => String -> Proxy m -> TestTree
mapTests name (_ :: Proxy m) =
    -- Чтобы можно было связать типовую переменную m здесь и в let ниже, нужно расширение ScopedTypeVariables.
    testGroup name [
        testGroup "Test toAscList . fromList" [
            testCase "toAscList . fromList sorts list" $
                let tr = fromList [(2, "a"), (1, "b"), (3, "c"), (1, "x")] :: m Int String in
                toAscList tr @?= [(1, "x"), (2, "a"), (3, "c")]
        ],
        testGroup "Test insert" [
            testCase "test insert in empty map" $
                let map = insert 1 "x" (empty :: m Int String)
                in Map.lookup 1 map @?= Just "x",

            testCase "test insert in not empty map" $
                let tr = fromList [(2, "a"), (3, "c"), (1, "x")] :: m Int String in
                let map = insert 4 "y" tr
                in Map.lookup 4 map @?= Just "y",

            testCase "test insertWith in not empty map" $
                let tr = fromList [(2, "a"), (3, "c"), (1, "x")] :: m Int String in
                let map = insertWith (++) 2 "x" tr
                in Map.lookup 2 map @?= Just "xa",

            testCase "test insertWithKey" $
                let f key new old = (show key) ++ ":" ++ new ++ "|" ++ old in
                let map           = insertWithKey f 5 "xxx" (fromList [(5,"a"), (3,"b")] :: m Int String)
                in Map.lookup 5 map @?= Just "5:xxx|a"
        ],
        testGroup "Test delete / adjust" [
            testCase "test delete" $
                let map = delete 3 (fromList [(2, "a"), (1, "b"), (3, "c"), (1, "x")] :: m Int String)
                in Map.lookup 3 map @?= Nothing,

            testCase "test delete from empty map" $
                let map = delete 5 (empty :: m Int String)
                in Map.null map @?= True,

            testCase "test adjust" $
               let map = adjust ("new " ++) 5 (fromList [(5,"a"), (3,"b")] :: m Int String)
               in Map.lookup 5 map @?= Just "new a",

            testCase "test adjustWithKey" $
               let f key x = (show key) ++ ":new " ++ x in
               let map     = adjustWithKey f 5 (fromList [(5,"a"), (3,"b")]) :: m Int String
               in Map.lookup 5 map @?= Just "5:new a"
        ],
        testGroup "Test update" [
            testCase "test update" $
                let f x = if x == "a" then Just "new a" else Nothing in
                let map = update f 5 (fromList [(5,"a"), (3,"b")]) :: m Int String in
                Map.lookup 5 map @?= Just "new a",

            testCase "test update single left" $
                let f x = if x == "a" then Just "new a" else Nothing in
                let map = update f 3 (fromList [(5,"a"), (3,"b")]) :: m Int String in
                Map.lookup 5 map @?= Just "a",

            testCase "test updateWithKey" $
                let f k x = if x == "a" then Just ((show k) ++ ":new a") else Nothing in
                let map   = updateWithKey f 5 (fromList [(5,"a"), (3,"b")]) :: m Int String
                in Map.lookup 5 map @?= Just "5:new a"
        ],
        testCase "alter" $
                let tr = fromList [(1, "a")] :: m Int String in
                toAscList (alter (const (Just "b")) 1 tr) @?= [(1, "b")]
        ,
        testGroup "Test member" [
            testCase "test member true" $
                let map = (fromList [(5,"a"), (3,"b")]) :: m Int String in
                member 5 map @?= True,

            testCase "test member false" $
                let map = (fromList [(5,"a"), (3,"b")]) :: m Int String in
                member 7 map @?= False,

            testCase "test notMember" $
                let map = (fromList [(5,"a"), (3,"b")]) :: m Int String in
                notMember 7 map @?= True,

            testCase "test notMember" $
                let map = (fromList [(5,"a"), (3,"b")]) :: m Int String in
                notMember 5 map @?= False
        ],
        testGroup "Test null" [
            testCase "test null true" $
                Map.null (empty :: m Int String) @?= True,

            testCase "test null false" $
                Map.null (fromList [(5,"a"), (3,"b")] :: m Int String) @?= False
        ]
    ]

testNaiveTree :: TestTree
testNaiveTree = testGroup "Test NaiveTree" [
        testGroup "merge" [
            testCase "merge empty" $
                merge Nil Nil @?= (Nil :: NaiveTree () ())
            ,
            testCase "merge two nodes" $
                -- Ваша реализация может выдавать другое дерево, соответствующее
                -- последовательности 1, 2.
                merge (Node 1 "a" Nil Nil) (Node 2 "b" Nil Nil)
                    @?= Node 1 "a" Nil (Node 2 "b" Nil Nil)
        ]
    ]

testMap :: TestTree
testMap = testGroup "Testing implementations of trees"
    [
        mapTests "Data.Map.Strict" (Proxy :: Proxy SMap.Map),
        mapTests "NaiveList" (Proxy :: Proxy NaiveList),
        mapTests "NaiveTree" (Proxy :: Proxy NaiveTree),
        testNaiveTree
    ]
